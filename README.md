# Distributed Banking System - gRPC
 Simple Distributed Banking System - gRPC
# To install grpc tools on Mac Terminal：
  $ python -m pip install grpcio
  $ python -m pip install grpcio-tools
# To compile .proto file to .py files: (update ... with .proto file directory)
  $ python -m grpc_tools.protoc -I... --python_out=. --grpc_python_out=. .../*.proto
# To execute file: 
 $ python main.py input.json
