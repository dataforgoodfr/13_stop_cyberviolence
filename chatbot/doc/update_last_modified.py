import re
import yaml
import sys

file, last_mod = sys.argv[1:3]

#iso date
last_mod = last_mod.split(" ")[0]

yaml_header_re = re.compile(r"(---)([.\s\S]*)(---)")

def upated_last_mod(file: str, last_mod: str):
    
    with open(file, 'r') as f:
        content = f.read()
    # print(yaml_header_re.match(content).groups())
    header = yaml.load(
        yaml_header_re.match(content).groups()[1].strip(),
        yaml.Loader
    )
    
    header['modified'] = last_mod
    
    with open(file, 'w') as f:
        f.write(
            yaml_header_re.sub(
                r'\1' + '\n' + yaml.dump(header) + r'\3',
                content
            )
        )
    
    return 1

if __name__ == "__main__":
    upated_last_mod(file, last_mod)