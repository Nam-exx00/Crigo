#Crigo Processor Commands
#Copyright (C) Nam_exx00,Max
#Date:2026-2-24-23:29
#No license now.

from amaranth import *
from amaranth.sim import Simulator

class Processor(Elaboratable):
    def __init__(self):
        self.temp = Signal(8)   #临时存储器
        self.mem = Memory(width=8, depth=256) #内存
        self.thiscom = Signal(8)    #当前命令
        self.pc = Signal(8)           # 处理器时间器
        self.target_addr = Signal(8)  # 地址指针
        self.rd_port = self.mem.read_port() #端口
    def elaborate(self,platform):   #硬编码の命令
        m = Module() 
        m.submodules.rd_port = self.rd_port # 提供端口
        m.d.comb += self.rd_port.addr.eq(self.pc) # 端口内读取地址
        m.d.sync += self.thiscom.eq(self.rd_port.data) # 端口内取数据
        m.d.sync += self.pc.eq(self.pc + 1)
        with m.Switch(self.thiscom):
            with m.Case(0): #啥都不做
                None
            with m.Case(1): #跳转        
                m.d.sync += self.pc.eq(self.temp)
        return m


if __name__ == '__main__':  #测试
    print('Crigo Processor Tests')
    cpu = Processor()
    cpu.mem.init = [1] + [0]*255
    sim = Simulator(cpu)
    sim.add_clock(1e-6)
    #那个Warning不用管，能跑就行。
    def tests():    #第一次test的PC一定要在0x42
        yield cpu.temp.eq(0x42) #设置临时存储器为0x42（目标地址）
        yield cpu.thiscom.eq(1)
        yield   #等待
        yield   #md还要等一次，不然0x01我服了。
        pc_value = yield cpu.pc
        print(f'PC is in:0x{pc_value:02X}')
        yield #再等一次
    def tests2():   #第二次的话，分别是0x44,0x45,0x46,0x47,0x48
        print("Crigo Processor Tests 2")
        for i in range(5):
            yield
            pc_val = yield cpu.pc
            print(f"Clock {i+1}, PC = 0x{pc_val:02X}")
    sim.add_sync_process(tests) #新建线程并调用测试
    sim.run()   #执行测试
    sim.add_sync_process(tests2) #新建线程并调用测试2
    sim.run()   #执行测试2 