from flask import Flask, render_template, request, jsonify
import alpha
import threading, time, os
# if thats the case
app = Flask(__name__)
sessions = {}
session_timestamps = {}
MAX_EXECUTION_TIME = 5

def cleanup_sessions():
    while True:
        now = time.time()
        for sid in list(session_timestamps.keys()):
            if now - session_timestamps[sid] > 600:
                sessions.pop(sid, None)
                session_timestamps.pop(sid, None)
        time.sleep(60)

threading.Thread(target=cleanup_sessions, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    code = request.form.get('code', '')
    session_id = request.form.get('session', 'default')
    input_value = request.form.get('input', None)
    input_var = request.form.get('input_var', None)

    session_timestamps[session_id] = time.time()
    input_values = sessions.get(session_id, {})

    if input_var and input_value is not None:
        input_values[input_var] = input_value

    sessions[session_id] = input_values
    result_container = {}

    def target():
        try:
            res = alpha.run_program_interactive(code, input_values)
            result_container['res'] = res
        except Exception as e:
            result_container['res'] = {'done': True, 'output': [], 'error': str(e)}

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(MAX_EXECUTION_TIME)

    if thread.is_alive():
        return jsonify({'done': True, 'output': [], 'error': f'Execution timed out ({MAX_EXECUTION_TIME}s).'})
    return jsonify(result_container['res'])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

