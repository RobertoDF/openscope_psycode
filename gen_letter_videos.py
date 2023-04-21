# A quick script to generate a video of a letter that blinks on and off. This is useful for testing since the actual
# experiment videos can be hard to see which video clip is which. Interestingly, this script was generated entirely
# from prompting ChatGPT-4 with the following prompt:
#
# I need to create three short videos that are stored as raw unsigned 8 bit integers in numpy format, .npy. I want
# each video to contain a blinking letter. Please use the letters A, B, and C, one for each video. The videos should be
# 2 seconds long and contain 120 total frames each. Can you write a python program to generate these videos as .npy
# files? Can you make it Python 2.7 valid code.

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def generate_blinking_letter_video(letter, filename):
    width, height = 64, 64  # Set the dimensions of the video frames
    fps = 60  # Set the frames per second
    num_frames = 120  # Set the total number of frames for a 2-second video
    on_duration = 15  # Set the number of frames the letter is visible
    off_duration = 15  # Set the number of frames the letter is invisible

    # Create an empty array to store the video data
    video_data = np.zeros((num_frames, height, width), dtype=np.uint8)

    # Create a font object
    font = ImageFont.truetype("arial.ttf", 40)

    for i in range(0, num_frames, on_duration + off_duration):
        for j in range(on_duration):
            if i + j < num_frames:
                frame = Image.new('L', (width, height), 0)  # Create a new blank image
                draw = ImageDraw.Draw(frame)
                text_width, text_height = draw.textsize(letter, font=font)
                position = ((width - text_width) // 2, (height - text_height) // 2)
                draw.text(position, letter, fill=255, font=font)
                video_data[i + j] = np.array(frame)

    # Save the video as a .npy file
    np.save(filename, video_data)

letters = ['A', 'B', 'C']

for letter in letters:
    generate_blinking_letter_video(letter, "data/{}_blinking_video.npy".format(letter))
    print("Generated data/{}_blinking_video.npy".format(letter))

print("Video generation complete!")
