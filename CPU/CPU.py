from amaranth import * #导入 Amaranth 框架的所有核心功能
from amaranth.sim import Simulator

import warnings
warnings.filterwarnings("ignore")

class Processor(Elaboratable): #定义一个新的处理器类，这个类是继承自Amaranth的Elaboratable基类
    def __init__(self): #类的构造函数（别称：初始化方法）
        self.temp = Signal(8) #临时存储器
        self.mem = Memory(width=8, depth=256, init=[1] + [0]*255)  #内存
        self.thiscom = Signal(8) #当前命令
        self.pc = Signal(8) #处理器时间器
        self.rd_port = self.mem.read_port() #端口

#=======================完美的分割线==========================

    def elaborate(self, platform): #硬编码搞事情的地方
        m = Module() #创建一个新的硬件模块容器
        m.submodules.rd_port = self.rd_port

        #取指阶段：组合逻辑读取内存
        m.d.comb += [
            self.rd_port.addr.eq(self.pc), #把PC的值连接到内存读取端口的地址线上
            self.thiscom.eq(self.rd_port.data)  #组合逻辑直接读取指令
        ]

        #执行阶段：同步逻辑更新PC
        with m.Switch(self.thiscom):
            with m.Case(0):  #NOP
                None
            with m.Case(1):  #JMP temp
                m.d.sync += self.pc.eq(self.temp)

        return m #回家吧孩子

#=======================完美的分割线==========================

if __name__ == '__main__': #练一练
    print('Crigo Processor Tests (Fixed v2)') #打印
    cpu = Processor() #创建一个处理器对象
    sim = Simulator(cpu) #创建一个仿真器
    sim.add_clock(1e-6) #为CPU添加一个时钟信号，设置时钟周期为1微秒

    def test_jump(): #试一试
        #初始化
        print(f"Initial PC = {yield cpu.pc}")
        
        #设置跳转目标
        yield cpu.temp.eq(0x42)
        print(f"Set temp = 0x{(yield cpu.temp):02X}")
        
        #第1个时钟：从pc=0取指(JMP)，pc自增到1
        yield 
        pc_val = yield cpu.pc
        thiscom_val = yield cpu.thiscom
        print(f"Clock 1: PC = 0x{pc_val:02X}, thiscom = 0x{thiscom_val:02X}")
        
        #第2个时钟：执行JMP指令，pc跳到0x42
        yield 
        pc_val = yield cpu.pc
        thiscom_val = yield cpu.thiscom
        print(f"Clock 2: PC = 0x{pc_val:02X}, thiscom = 0x{thiscom_val:02X}")
        
        #第3个时钟：从pc=0x42取指(NOP)，pc自增到0x43
        yield 
        pc_val = yield cpu.pc
        thiscom_val = yield cpu.thiscom
        print(f"Clock 3: PC = 0x{pc_val:02X}, thiscom = 0x{thiscom_val:02X}")
        
        #第4个时钟：执行NOP指令，pc自增到0x44
        yield 
        pc_val = yield cpu.pc
        print(f"Clock 4: PC = 0x{pc_val:02X}")

    sim.add_sync_process(test_jump)   #把写好的测试指南交给仿真器，准备干活
    sim.run() #启动
