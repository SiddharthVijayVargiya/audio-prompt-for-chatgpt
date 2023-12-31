import sounddevice as sd
import numpy as np
import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer
import openai

def record_audio(duration, sample_rate=16000):
    print(f"Recording audio for {duration} seconds...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()  # Wait for recording to complete
    print("Recording finished.")
    return audio

def transcribe_audio(audio, model, tokenizer, sample_rate=16000):
    audio_mono = np.mean(audio, axis=1)
    audio_mono /= np.max(np.abs(audio_mono))

    # Load the audio into a PyTorch tensor
    input_values = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16_000)(torch.FloatTensor(audio_mono))

    # Perform speech recognition
    with torch.no_grad():
        input_values = input_values.unsqueeze(0)
        logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)

    transcription = tokenizer.batch_decode(predicted_ids)[0]
    return transcription
    # ... (same as in the previous code)

if __name__ == "__main__":
    duration = 20  # Duration in seconds

    # Load pretrained model and tokenizer
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
    tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")

    # Record and transcribe audio
    audio_data = record_audio(duration)
    transcription = transcribe_audio(audio_data, model, tokenizer)
    print("Transcription:", transcription)

    # Set your OpenAI API key here
    openai.api_key = "YOUR_OPENAI_API_KEY"

    # Generate improved text using OpenAI API
    prompt = f"Please help improve the grammar of the following text: '{transcription}'"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )

    if response.status == 200:
        improved_text = response.choices[0].text.strip()
        print("Improved Text:", improved_text)
    else:
        print("Error: Unable to generate improved text using OpenAI API")

