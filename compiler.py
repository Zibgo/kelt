#kelt v1.1
import json
from generator import Generator
from kvm import KVM

class Compiler:
    def __init__(self, text):
        self.text = text
        self.generator = Generator(text)
        self.vm = KVM()

    def run(self):
        code = self.generator.generate_code()
        self.vm.check_labels(code)
        return self.vm.run()

c = Compiler('''use io;
fn add[a, b]
{
ret a + b;
}

fn main[]
{
x = 15; #pwqrwe huj
global y = 10;

z = add[x, y];

print[z];

n = read[];
print[n];
}''')

c.run()
