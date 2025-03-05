from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import os
import io
import subprocess
import re
import platform
import atexit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitoring.db'
db = SQLAlchemy(app)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    is_ip = db.Column(db.Boolean, default=False)  # Indica se é um IP ou URL
    logs = db.relationship('MonitoringLog', backref='link', lazy='dynamic', order_by='desc(MonitoringLog.timestamp)', cascade='all, delete-orphan')

class MonitoringLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('link.id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    status_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)  # Tempo de resposta em segundos
    is_up = db.Column(db.Boolean)
    packet_loss = db.Column(db.Float)  # Percentual de perda de pacotes
    latency = db.Column(db.Float)  # Latência em ms
    jitter = db.Column(db.Float)  # Variação da latência em ms

def calculate_jitter(times):
    """
    Calcula o jitter como a média das diferenças absolutas entre tempos consecutivos
    RFC 3550 método de cálculo
    """
    if len(times) < 2:
        return 0
        
    differences = []
    for i in range(1, len(times)):
        difference = abs(times[i] - times[i-1])
        differences.append(difference)
    
    return sum(differences) / len(differences)

def ping(host):
    """
    Executa ping para um host e retorna latência, perda de pacotes e jitter
    """
    try:
        print(f"Executando ping para {host}...")  # Debug
        if platform.system().lower() == "windows":
            command = ['ping', '-n', '3', host]
        else:
            command = ['ping', '-c', '3', host]
            
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        output = result.stdout
        print(f"Saída do ping:\n{output}")  # Debug
        
        # Extraindo informações do ping
        times = []
        if platform.system().lower() == "windows":
            time_matches = re.findall(r"tempo[<=](\d+)ms", output)
        else:
            time_matches = re.findall(r"time[<=](\d+\.\d+) ms", output)
            
        for match in time_matches:
            times.append(float(match))
        
        print(f"Tempos extraídos: {times}")  # Debug
        
        # Calculando métricas
        sent = 3
        received = len(times)
        packet_loss = ((sent - received) / sent) * 100
        
        if times:
            latency = sum(times) / len(times)
            jitter = calculate_jitter(times)
        else:
            latency = 0
            jitter = 0
            
        result = {
            'success': received > 0,
            'latency': latency,
            'packet_loss': packet_loss,
            'jitter': jitter
        }
        print(f"Resultado do ping: {result}")  # Debug
        return result
    except Exception as e:
        print(f"Erro ao executar ping para {host}: {str(e)}")  # Debug
        return {
            'success': False,
            'latency': 0,
            'packet_loss': 100,
            'jitter': 0
        }

def check_links():
    print("Iniciando verificação dos links...")  # Debug
    with app.app_context():
        links = Link.query.filter_by(active=True).all()
        for link in links:
            try:
                if link.is_ip:
                    print(f"Verificando IP {link.url}...")  # Debug
                    # Usando ping para IPs
                    result = ping(link.url)
                    print(f"Resultado do ping para {link.url}: {result}")  # Debug
                    log = MonitoringLog(
                        link_id=link.id,
                        status_code=200 if result['success'] else 0,
                        response_time=result['latency'] / 1000,  # Convertendo ms para segundos
                        is_up=result['success'],
                        packet_loss=result['packet_loss'],
                        latency=result['latency'],
                        jitter=result['jitter']
                    )
                else:
                    print(f"Verificando URL {link.url}...")  # Debug
                    # Usando HTTP para URLs
                    times = []
                    success = 0
                    for _ in range(3):
                        try:
                            start_time = datetime.now()
                            response = requests.get(link.url, timeout=10)
                            response_time = (datetime.now() - start_time).total_seconds()
                            times.append(response_time * 1000)  # Convertendo para ms
                            if response.status_code == 200:
                                success += 1
                        except:
                            times.append(None)
                    
                    valid_times = [t for t in times if t is not None]
                    packet_loss = ((3 - len(valid_times)) / 3) * 100
                    
                    if valid_times:
                        avg_latency = sum(valid_times) / len(valid_times)
                        jitter = calculate_jitter(valid_times)
                        response_time = valid_times[0] / 1000  # Primeiro tempo em segundos
                    else:
                        avg_latency = 0
                        jitter = 0
                        response_time = 0
                    
                    is_up = success > 0
                    
                    log = MonitoringLog(
                        link_id=link.id,
                        status_code=response.status_code if is_up else 0,
                        response_time=response_time,
                        is_up=is_up,
                        packet_loss=packet_loss,
                        latency=avg_latency,
                        jitter=jitter
                    )
                
                db.session.add(log)
                db.session.commit()
                print(f"Log salvo para {link.url}: status={'online' if log.is_up else 'offline'}")  # Debug
            except Exception as e:
                print(f"Erro ao verificar {link.url}: {str(e)}")  # Debug
                log = MonitoringLog(
                    link_id=link.id,
                    status_code=0,
                    response_time=0,
                    is_up=False,
                    packet_loss=100,
                    latency=0,
                    jitter=0
                )
                db.session.add(log)
                db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_link', methods=['POST'])
def add_link():
    url = request.form.get('url')
    description = request.form.get('description')
    is_ip = request.form.get('is_ip', 'false') == 'true'
    
    # Remove http:// ou https:// se for IP
    if is_ip:
        url = url.replace('http://', '').replace('https://', '')
        # Remove qualquer path após o IP
        url = url.split('/')[0]
    else:
        # Adiciona https:// se não tiver protocolo
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
    
    link = Link(url=url, description=description, is_ip=is_ip)
    db.session.add(link)
    db.session.commit()
    
    flash('Link adicionado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/view_logs/<int:link_id>')
def view_logs(link_id):
    link = Link.query.get_or_404(link_id)
    logs = MonitoringLog.query.filter_by(link_id=link_id).order_by(MonitoringLog.timestamp.desc()).all()
    return render_template('logs.html', link=link, logs=logs)

@app.route('/export_pdf/<int:link_id>')
def export_pdf(link_id):
    link = Link.query.get_or_404(link_id)
    logs = MonitoringLog.query.filter_by(link_id=link_id).order_by(MonitoringLog.timestamp.desc()).all()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    data = [['Data/Hora', 'Status', 'Tempo de Resposta (s)', 'Online']]
    for log in logs:
        data.append([
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            str(log.status_code),
            f"{log.response_time:.2f}" if log.response_time else "N/A",
            "Sim" if log.is_up else "Não"
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'monitoring_report_{link.id}_{datetime.now().strftime("%Y%m%d")}.pdf',
        mimetype='application/pdf'
    )

@app.route('/api/metrics/<int:link_id>')
def get_metrics(link_id):
    hours = request.args.get('hours', 24, type=int)
    since = datetime.now() - timedelta(hours=hours)
    
    logs = MonitoringLog.query.filter(
        MonitoringLog.link_id == link_id,
        MonitoringLog.timestamp >= since
    ).order_by(MonitoringLog.timestamp.asc()).all()
    
    data = {
        'timestamps': [log.timestamp.strftime('%Y-%m-%d %H:%M:%S') for log in logs],
        'latency': [log.latency for log in logs],
        'packet_loss': [log.packet_loss for log in logs],
        'jitter': [log.jitter for log in logs],
        'status': [log.is_up for log in logs]
    }
    
    return jsonify(data)

@app.route('/api/links')
def get_links():
    links = Link.query.all()
    links_data = []
    
    for link in links:
        last_log = link.logs.first()
        links_data.append({
            'id': link.id,
            'url': link.url,
            'description': link.description,
            'is_up': last_log.is_up if last_log else False,
            'active': link.active
        })
    
    return jsonify(links_data)

@app.route('/delete_link/<int:link_id>', methods=['POST'])
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash('Link removido com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/edit_link/<int:link_id>', methods=['GET', 'POST'])
def edit_link(link_id):
    link = Link.query.get_or_404(link_id)
    
    if request.method == 'POST':
        url = request.form.get('url')
        is_ip = request.form.get('is_ip', 'false') == 'true'
        
        # Remove http:// ou https:// se for IP
        if is_ip:
            url = url.replace('http://', '').replace('https://', '')
            # Remove qualquer path após o IP
            url = url.split('/')[0]
        else:
            # Adiciona https:// se não tiver protocolo
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'https://' + url
        
        link.url = url
        link.description = request.form.get('description')
        link.is_ip = is_ip
        link.active = request.form.get('active', 'false') == 'true'
        
        db.session.commit()
        flash('Link atualizado com sucesso!', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit_link.html', link=link)

@app.route('/toggle_active/<int:link_id>', methods=['POST'])
def toggle_active(link_id):
    link = Link.query.get_or_404(link_id)
    link.active = not link.active
    db.session.commit()
    status = "ativado" if link.active else "desativado"
    flash(f'Monitoramento {status} com sucesso!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
    # Criar o scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_links, trigger="interval", seconds=30)
    scheduler.start()
    
    # Registrar função para parar o scheduler quando a aplicação for encerrada
    atexit.register(lambda: scheduler.shutdown())
    
    app.run(debug=True, use_reloader=False)
