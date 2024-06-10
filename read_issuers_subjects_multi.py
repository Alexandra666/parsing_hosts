from subprocess import check_output, CalledProcessError
import sys
import multiprocessing


def main():
    addresses = get_file_content()
    result, error = create_responses(addresses)
    with open(sys.argv[2], "a") as output_file:
        for r in result:
            output_file.write(r)
    with open("wrong_hosts_443.txt", "a") as error_file:
        for err in error:
            error_file.write(err)


def get_file_content():
    file_content = []
    if len(sys.argv) < 3:
        sys.exit(
            "Too few arguments, use the following template <source_file> <output_file>"
        )
    if len(sys.argv) > 3:
        sys.exit(
            "Too many arguments, use the following template <source_file> <output_file>"
        )
    else:
        try:
            with open(sys.argv[1]) as file:
                for line in file:
                    if "\n" in line:
                        line = line[:-1]
                    file_content.append(line)
            return file_content
        except FileNotFoundError:
            sys.exit(f"{sys.argv[1]} does not exist")


def work(variable):
    print(
        f"Process {multiprocessing.current_process().name} started working on task {variable}",
        flush=True,
    )

    cmd = f"echo | openssl s_client -showcerts -servername {variable} -connect {variable}:443 2>/dev/null | openssl x509 -inform pem -noout -text | egrep 'Issuer:|Subject:'"
    print(
        f"Process {multiprocessing.current_process().name} ended working on task {variable}",
        flush=True,
    )
    return check_output(cmd, shell=True)


def create_responses(addresses_list):
    results = []
    errors = []
    count = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=count) as p:
        iterator = p.imap(work, addresses_list)
        while True:
            try:
                results.append(next(iterator).decode("utf-8").lstrip())
            except StopIteration:
                break
            except CalledProcessError as e:
                error_address = repr(e).split()[7]
                print(f"Host {error_address} does not exist")
                errors.append(error_address + "\n")

    return results, errors


if __name__ == "__main__":
    main()
