from flask import Flask, request, jsonify
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
async def upload_file(writer):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400  # Bad Request

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400  # Bad Request

    if file:
        filename = os.path.join('uploads', file.filename)
        file.save(filename)
        
        # Get file size
        file_size = os.path.getsize(filename)
        
        # filename and file size
        #file_info = jsonify({
        #   'filename': file.filename,
        #   'size': file_size
        #}), 200  # OK
        info_message = f"{file.filename}\n{file_size}\n"
        try:
            writer.write(info_message.encode())
            await writer.drain()
            print(f"Sent file info to server: {info_message}")
        except Exception as e:
            print(f"Error sending file info{e}")
        finally:
            writer.close()
            return info_message

if __name__ == '__main__':
    app.run(debug=True)