import edge_tts
import asyncio
import platform
import os
import pygame

# 检查系统类型
if platform.system() == 'Linux':  # Raspberry Pi 运行的是 Linux 系统
    import pygame


# 生成音频并保存为本地文件，支持语速控制
async def generate_and_save_tts(text, voice, output_file, speed="+0%"):  # 新增速度参数
    # 正确格式化 SSML 文本
    communicate = edge_tts.Communicate(text=text, voice=voice,rate=speed)  # 通过 `text` 参数传递 SSML 格式化的内容
    await communicate.save(output_file)
    print(f"Audio saved as: {output_file}")

# 播放本地音频文件
def play_audio_file(file_path):
    if platform.system() in ['Linux', 'Darwin']:  # 在树莓派或 macOS 上运行
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        # 等待音频播放结束
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        print(f"Audio playback finished: {file_path}")
    else:
        print(f"Audio playback is not supported on this system: {platform.system()}")

# 示例使用：生成多语言音频
if __name__ == "__main__":

    # 调整速度为较快
    asyncio.run(generate_and_save_tts("Face image saved successfully", "en-US-GuyNeural",
                                      "../static/audio/save_success.mp3", speed="-25%"))
    # 调整速度为非常快
    asyncio.run(generate_and_save_tts("Face verification succeeded, the locker will be opened.", "en-US-GuyNeural",
                                      "../static/audio/verify_success.mp3", speed="-25%"))
    asyncio.run(generate_and_save_tts("Face verification failed, please try again.", "en-US-GuyNeural",
                                      "../static/audio/verify_fail.mp3", speed="-25%"))
