from setuptools import setup, find_packages

setup(
    name='go2-webrtc-connect',
    version='1.0.0',
    author='legion1581',
    author_email='legion1581@gmail.com',
    description='Unitree Go2 Web Interface with WebRTC Control',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        # Core Web Framework
        'Flask>=3.0.0',
        'Flask-CORS>=4.0.0',
        
        # Computer Vision
        'numpy>=1.26.0,<2.0.0',
        'opencv-python>=4.10.0',
        
        # WebRTC and Media Processing
        'aiortc>=1.9.0',
        'aiohttp>=3.10.0',
        'av>=13.1.0',
        'websockets>=13.0',
        
        # go2_webrtc_driver Dependencies
        'requests>=2.31.0',
        'pycryptodome>=3.19.0',
        'pyaes>=1.6.1',
        'wasmtime>=14.0.0',
        'protobuf>=4.25.0',
        'pynacl>=1.5.0',
        'lz4>=4.3.2',
        'sounddevice>=0.4.6',
        
        # Build Tools
        'setuptools>=70.0.0',
        
        # Unitree WebRTC Driver (from GitHub)
        'go2-webrtc-driver @ git+https://github.com/legion1581/unitree_webrtc_connect.git',
    ],
)
