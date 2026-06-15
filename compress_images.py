from PIL import Image
import os

def compress_gif(input_path, output_path, min_size_mb=0.9, max_size_mb=1.0):
    min_size_bytes = min_size_mb * 1024 * 1024
    max_size_bytes = max_size_mb * 1024 * 1024
    
    with Image.open(input_path) as img:
        if img.format != 'GIF':
            img.save(output_path)
            return
        
        frames = []
        durations = []
        n_frames = getattr(img, 'n_frames', 1)
        
        try:
            while True:
                frames.append(img.copy())
                durations.append(img.info.get('duration', 100))
                img.seek(img.tell() + 1)
        except EOFError:
            pass
        
        target_frames = 50
        if n_frames > target_frames:
            frame_skip = n_frames // target_frames
            frames = frames[::frame_skip]
            durations = durations[::frame_skip]
        
        new_size = (500, 120)
        frames = [f.resize(new_size, Image.Resampling.LANCZOS) for f in frames]
        
        for colors in [256, 200, 180, 160, 140, 128, 110, 100, 90, 80, 70, 64]:
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                optimize=True,
                colors=colors
            )
            
            size = os.path.getsize(output_path)
            if min_size_bytes <= size <= max_size_bytes:
                print(f"OK {os.path.basename(input_path)} -> {size/1024/1024:.2f}MB (frames: {len(frames)}, colors: {colors})")
                return
            elif size < min_size_bytes:
                print(f"Small {os.path.basename(input_path)} -> {size/1024/1024:.2f}MB (frames: {len(frames)}, colors: {colors}) - trying fewer colors")
        
        for quality in [95, 90, 85, 80, 75, 70]:
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                optimize=True,
                quality=quality,
                colors=128
            )
            
            size = os.path.getsize(output_path)
            if min_size_bytes <= size <= max_size_bytes:
                print(f"OK {os.path.basename(input_path)} -> {size/1024/1024:.2f}MB (frames: {len(frames)}, quality: {quality})")
                return
        
        size = os.path.getsize(output_path)
        print(f"Final {os.path.basename(input_path)} -> {size/1024/1024:.2f}MB (frames: {len(frames)}) - closest achieved")

def main():
    images_dir = "images/Assinaturas"
    for filename in os.listdir(images_dir):
        if filename.lower().endswith('.gif') and filename != 'desktop.ini':
            input_path = os.path.join(images_dir, filename)
            output_path = os.path.join(images_dir, filename)
            
            original_size = os.path.getsize(input_path) / 1024 / 1024
            print(f"Processing {filename} ({original_size:.2f}MB)...")
            
            compress_gif(input_path, output_path)
            
            new_size = os.path.getsize(output_path) / 1024 / 1024
            print(f"  Done: {original_size:.2f}MB -> {new_size:.2f}MB")

if __name__ == "__main__":
    main()