from pydub import AudioSegment

# Load the audio file
audio = AudioSegment.from_file("red_light_2.wav")  # Replace with your file path

# Create silence (duration in milliseconds)
silence_duration = 2000  # 2 seconds
silence = AudioSegment.silent(duration=silence_duration)

# Add silence to the beginning or end
padded_audio = silence + audio  # Silence at the beginning
# padded_audio = audio + silence  # Silence at the end

# Export the padded audio
padded_audio.export("red_light_2_padded.wav", format="wav")  # Replace with desired format
