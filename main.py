import argparse
import json
import multiprocessing
from time import sleep
from concurrent import futures

import grpc

import branch_pb2_grpc
from Branch import Branch
from Customer import Customer


# To start gRPC server process for branch
def serveBranch(branch):
    branch.createStubs()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    branch_pb2_grpc.add_BranchServicer_to_server(branch, server)
    port = str(10000 + branch.id)
    server.add_insecure_port("[::]:" + port)
    server.start()
    server.wait_for_termination()


# To start customer gRPC client processes
def serveCustomer(customer):
    customer.createStub()
    customer.executeEvents()

    output = customer.output()
    output_file = open("output.txt", "a")
    output_file.write(str(output) + "\n")
    output_file.close()


# Parse input & create objects/processes
def createProcesses(processes):
    customers = []
    customerProcesses = []
    branches = []
    branchIds = []
    branchProcesses = []

    # Instialize Branch objects
    for process in processes:
        if process["type"] == "branch":
            branch = Branch(process["id"], process["balance"], branchIds)
            branches.append(branch)
            branchIds.append(branch.id)

    # Go through Branch processes
    for branch in branches:
        branch_process = multiprocessing.Process(target=serveBranch, args=(branch,))
        branchProcesses.append(branch_process)
        branch_process.start()

    # Timer delay for branch processes to start
    sleep(0.3)

    # Intialize Customer objects
    for process in processes:
        if process["type"] == "customer":
            customer = Customer(process["id"], process["events"])
            customers.append(customer)

    # Go through Customer processes
    for customer in customers:
        customer_process = multiprocessing.Process(target=serveCustomer, args=(customer,))
        customerProcesses.append(customer_process)
        customer_process.start()

    # Wait for Customer processes to complete
    for customerProcess in customerProcesses:
        customerProcess.join()

    # Terminate Branch processes
    for branchProcess in branchProcesses:
        branchProcess.terminate()


if __name__ == "__main__":
    # argument for 'input_file'
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    args = parser.parse_args()

    try:
        # Load JSON file from 'input_file' arg
        input = json.load(open(args.input_file))

        # Initialize output file
        open("output.txt", "w").close()

        # Create objects/processes from input file
        createProcesses(input)
    except FileNotFoundError:
        print(colored("Could not find input file '" + args.input_file + "'", "red"))
    except json.decoder.JSONDecodeError:
        print(colored("Error decoding JSON file", "red"))
