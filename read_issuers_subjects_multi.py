from subprocess import check_output, CalledProcessError
import sys
import multiprocessing


def main():
    addresses, port_number = get_file_content()
    result, error = create_responses(addresses, port_number)
    with open(sys.argv[2], "a") as output_file:
        for r in result:
            output_file.write(r)
    with open(f"wrong_hosts_{port_number}.txt", "a") as error_file:
        for err in error:
            error_file.write(err)


def get_file_content():
    file_content = []
    if len(sys.argv) < 4:
        sys.exit(
            "Too few arguments, use the following template <source_file> <output_file> <port_number>"
        )
    if len(sys.argv) > 4:
        sys.exit(
            "Too many arguments, use the following template <source_file> <output_file> <port_number> "
        )
    else:
        try:
            with open(sys.argv[1]) as file:
                for line in file:
                    if "\n" in line:
                        line = line[:-1]
                    file_content.append(line)
            port = int(sys.argv[3])
            return file_content, port
        except FileNotFoundError:
            sys.exit(f"{sys.argv[1]} does not exist")
        except ValueError:
            sys.exit("Invalid port number")


def work(variable, port):
    try:
        print(
            f"Process {multiprocessing.current_process().name} started working on task {variable}",
            flush=True,
        )

        cmd = f"echo | openssl s_client -showcerts -servername {variable} -connect {variable}:{port} 2>/dev/null | openssl x509 -inform pem -noout -text | egrep 'Issuer:|Subject:'"
        print(
            f"Process {multiprocessing.current_process().name} ended working on task {variable}",
            flush=True,
        )
        return check_output(cmd, shell=True).decode("utf-8").lstrip()
    except CalledProcessError as e:
        return repr(e).split()[7]


def create_responses(addresses_list, port):
    results = []
    errors = []
    count = multiprocessing.cpu_count()
    args = [[address, port] for address in addresses_list]
    with multiprocessing.Pool(processes=count) as p:
        for result in p.starmap(work, args):
            if not result.startswith("Issuer:") and "Subject:" not in result:
                print(f"Host {result} does not exist on port {port}")
                errors.append(result + "\n")
            else:
                results.append(result)
    return results, errors


if __name__ == "__main__":
    main()
