from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import config  # Make sure you have your OPENAI_API_KEY in a config file or environment variable

app = Flask(__name__)

client = OpenAI(api_key = config.OPENAI_API_KEY)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    url = request.form['url']
    video_id = url.split('v=')[-1]

    try:
        # Download the transcript from the YouTube video
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_generated_transcript(['en']).fetch()

        # Extract and concatenate all text elements
        concatenated_text = " ".join(item['text'] for item in transcript)

        # Call the OpenAI ChatCompletion endpoint, with the ChatGPT model
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Summarize the following text."},
                {"role": "assistant", "content": "Yes."},
                {"role": "user", "content": concatenated_text}
            ]
        )

        summary = response.choices[0].message['content']
        return jsonify({'summary': summary})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)


