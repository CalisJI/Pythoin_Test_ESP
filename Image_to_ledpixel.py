from PIL import Image
import json

def convert_image_to_led_matrix_format(image_path):
    # Open the image
    img = Image.open(image_path)
    
    # Ensure the image is in RGB format
    img = img.convert('RGB')
    
    # Get image dimensions
    width, height = img.size
    
    # Initialize the list to store pixel values
    pixel_data = []
    
    # Iterate over each pixel
    for y in range(height):
        for x in range(width):
            # Get RGB values
            R, G, B = img.getpixel((x, y))
            # Append the dictionary with pixel details to the list
            pixel_data.append({
                'x': x,
                'y': y,
                'R': R,
                'G': G,
                'B': B
            })
    
    return pixel_data

# Example usage
image_path = 'path_to_your_image.png'
led_matrix_data = convert_image_to_led_matrix_format(image_path)

# Convert the list of pixel data to JSON format
led_matrix_data_json = json.dumps(led_matrix_data, indent=4)

# Print the JSON result
print(led_matrix_data_json)

# Optionally, save the JSON data to a file
with open('led_matrix_data.json', 'w') as json_file:
    json_file.write(led_matrix_data_json)
