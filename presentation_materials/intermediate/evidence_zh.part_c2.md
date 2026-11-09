## 6. 速度提升主要来自哪些修改和机制?

### 6.1 哪些函数反复成为赢家,各自做了什么(重新阅读了实际补丁)

下表统计**最终补丁**里包含哪些函数的改动(种群搜索:谱系上的全部祖先,因为子补丁继承;greedy:全部被接受的步骤;best-of-N:单个函数)。每个配置 5 个最终补丁:

| 配置 | 最终补丁中最常出现的函数(出现次数/5) |
|---|---|
| Qwen 种群搜索 (I1) | Profile::GetMesg (4/5); Field::GetType (4/5); FieldBase::GetNumValues (2/5); FieldBase::FieldBase (2/5); AccumulatedField::AccumulatedField (1/5); IsAvgNegGradeValid (1/5) |
| Qwen best-of-N (I1) | Profile::GetMesg (4/5); FieldBase::FieldBase (1/5) |
| Qwen 种群搜索 (I3, README 循环) | Profile::GetMesg (4/5); FieldBase::FieldBase (3/5); Field::GetType (3/5); Mesg::GetField (2/5); Decode::Resume (2/5); Field::GetNum (2/5) |
| Qwen best-of-N (I3, 匹配对照) | Profile::GetMesg (5/5) |
| DeepSeek greedy 单链 (I2) | Profile::GetMesg (5/5); FieldBase::FieldBase (5/5); FieldBase::GetValue (4/5); Profile::GetFieldIndex (4/5); Mesg::GetField (3/5); Field::GetNum (2/5) |
| DeepSeek best-of-N (I2, 排序规则) | Profile::GetMesg (5/5) |
| DeepSeek 种群搜索 (I3, README 循环) | FieldBase::FieldBase (5/5); Profile::GetMesg (4/5); FieldBase::GetNumValues (3/5); Field::GetType (2/5); Field::GetNum (2/5); Profile::GetFieldIndex (2/5) |
| DeepSeek best-of-N (I3, 匹配对照) | Profile::GetMesg (5/5) |

**所有 DeepSeek 的 best-of-N 最终补丁(两个版本共 10 个)都只改 `Profile::GetMesg`**(speedup 1.067–1.074);Qwen 的 best-of-N 最终补丁 10 个里 9 个也是 `Profile::GetMesg`,另一个(I1 种子 2)是 `FieldBase::FieldBase`。`GetMesg` 是 profile 里最热的函数(约 19% 的样本),把线性扫描换成查表就是最容易找到的单点赢家。种群搜索和 greedy 的赢家集合更大:`Profile::GetMesg`、`FieldBase::FieldBase`(拷贝构造)、`Profile::GetFieldIndex`、`FieldBase::GetValue`、`Mesg::GetField`/`AddField` 等。

**常见优化各自减少了什么工作**(以 greedy 种子 3 链的实际补丁为例,逐个读了 diff;“消息”表示只读了补丁头部的说明):

| 函数 | 核对方式 | 减少了什么工作 | 搜索时单步收益 |
|---|---|---|---|
| `Profile::GetMesg` | 读 diff(0005、0011) | **查找**:线性扫描 124 项 → 65536 项表(或排序表)一次读取 | 最大的单步,约 6%(搜索时) |
| `Profile::GetFieldIndex` | 读 diff(0003) | **查找**:字段号线性扫描 → 位图+下标表缓存(缓存最近一个消息类型) | 搜索时约 1.5%;引入并发错误(见 §7) |
| `FieldBase::FieldBase`(拷贝构造) | 读 diff(0004) | **分配与复制**:原来先默认构造两个 `vector` 再赋值;现在在成员初始化列表里直接拷贝构造,省掉一次构造+一次赋值(字段在构造消息时被大量拷贝) | 搜索时约 4.4%(1 行改动) |
| `FieldBase::GetValue` | 读 diff(0010) | **逐字节拼装 → 一次 `memcpy`**(按 1/2/4/8 字节分支);假设小端机器 | 搜索时约 0.7% |
| `Mesg::AddField` | 读 diff(0008) | **函数调用**:内联扫描已有字段,省掉对 `GetField` 的调用与返回指针 | 搜索时约 1.4% |
| `CRC::Get16` | 读 diff(0007) | **查表次数减半**:16 项半字节表 → 256 项按字节的 constexpr 表 | 搜索时约 0.25% |
| `Decode::Resume` | 读 diff(0002) | **成员读写 → 局部变量**(可放寄存器),在跳出循环时才写回 | 搜索时约 0.4% |
| `Field::GetType`、`GetNumSubFields`、`MesgDefinition::GetFieldByIndex`、`MesgBroadcaster::RemoveListener` | 消息(0001、0006、0009、0012) | 改写形式或加分支提示,**几乎没有减少工作**;补丁说明自己也承认在噪声内(0.03%–0.16%) | 与 §3.4 的空搜索噪声同量级 |

所以收益的主要来源是**三类**:消灭线性查找(`GetMesg`、`GetFieldIndex`)、减少构造/拷贝(`FieldBase` 拷贝构造)、把逐字节循环换成宽访问(`GetValue`)。其余多为噪声级的小步。

### 6.2 一条有代表性的累计链(DeepSeek greedy,种子 3,中位数种子)

| 步骤 | 请求/代 | 函数 | 搜索时累计 speedup(记录) | 单步收益(相对上一个记录) | 是否独立复测 | 该步骤的扩展正确性(步骤 1–11 和第 12 步(旧最终状态)测过;第 13 步未测) |
|---|---|---|---|---|---|---|
| 1 | 6 | MesgBroadcaster::RemoveListener | 1.0010 | 0.10% | 否 | TSan 0 处;无并发不一致 |
| 2 | 11 | Decode::Resume | 1.0047 | 0.37% | 否 | TSan 0 处;无并发不一致 |
| 3 | 12 | Profile::GetFieldIndex | 1.0200 | 1.50% | 否 | TSan 3 处;4 线程下 36 次与单线程不一致 |
| 4 | 13 | FieldBase::FieldBase | 1.0673 | 4.43% | 否 | TSan 2 处;4 线程下 38 次与单线程不一致 |
| 5 | 17 | Profile::GetMesg | 1.1370 | 6.12% | 否 | TSan 3 处;4 线程运行未完成 |
| 6 | 18 | Field::GetType | 1.1373 | 0.03% | 否 | TSan 3 处;4 线程运行未完成 |
| 7 | 20 | CRC::Get16 | 1.1402 | 0.25% | 否 | TSan 3 处;4 线程运行未完成 |
| 8 | 21 | Mesg::AddField | 1.1561 | 1.38% | 否 | TSan 3 处;4 线程下 39 次与单线程不一致 |
| 9 | 28 | MesgDefinition::GetFieldByIndex | 1.1580 | 0.16% | 否 | TSan 3 处;4 线程下 39 次与单线程不一致 |
| 10 | 31 | FieldBase::GetValue | 1.1661 | 0.69% | 否 | TSan 2 处;4 线程下 38 次与单线程不一致 |
| 11 | 34 | Profile::GetMesg | 1.1675 | 0.12% | 否 | TSan 4 处;4 线程运行未完成 |
| 12 | 37 | Field::GetNumSubFields | 1.1683 | 0.06% | 否 | TSan 4 处;4 线程运行未完成(= 旧最终状态 final-greedy-seed3) |
| 13 | 39 | Mesg::GetField | 1.1766 | 0.71% | 是(仅最终补丁) |  |

**读这张表的规则:** (1) “搜索时累计 speedup”是**整个累计补丁**相对原库的 speedup(1/R),单步收益是记录的相对变化,**不能把各步百分比直接相加**,更不能把后面每一轮“继承了前面的收益”都算成一次新发现;(2) 只有最后一个数(1.1758,40 请求最终补丁的 3 次独立复测)是独立确认的;中间各步只有搜索时的两次测量;(3) 13 步里有 5 步(1、6、9、11、12)小于 0.2%,其中 2 步(6、12)不大于空搜索观察到的最大噪声单步 0.063%——它们在最终补丁里,但很可能没有贡献;(4) 步骤 3 引入 `GetFieldIndex` 缓存的那一步是**最早出现并发错误输出的补丁**(§7)。链上总共 40 个请求里只有 13 个被接受。

### 6.3 best-of-N 候选的组合

**做法(没有新的模型调用):** 取一个 DeepSeek best-of-N(I2)运行已经产生的全部候选;**每个函数**留搜索时 ratio 最低且 < 1 的那个候选;按搜索时 ratio 从好到坏排序;依次把前 K 个叠在一起(一个与已叠补丁冲突、不能干净应用的候选会被跳过并记录——5 个种子里只有种子 5 跳过 1 个);每个叠加状态用冻结的测量程序独立测 3 次(同时跑课程自带检查)。这 5 个种子共构造并测了 56 个叠加状态、168 次独立测量,**新增的模型调用为 0**。

| 种子 | 可用候选函数数 | best-of-N 最终(单函数) | 固定 K=2 | 固定 K=3 | 固定 K=5 | **事后**最佳 K | 最佳 K 的 speedup(事后选择) | 叠到最后一个候选 | 该种子 greedy(40 请求) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 11 | 1.0730 | 1.1304 | 1.1427 | 1.1421 | 9 | 1.1632 | 1.1557 | 1.1574 |
| 2 | 10 | 1.0688 | 1.1217 | 1.1358 | 1.1922 | 6 | 1.1977 | 1.1924 | 1.2155 |
| 3 | 13 | 1.0740 | 1.1272 | 1.1363 | 1.1464 | 10 | 1.1579 | 1.1574 | 1.1758 |
| 4 | 12 | 1.0725 | 1.1310 | 1.1499 | 1.1578 | 7 | 1.1870 | 1.1769 | 1.1919 |
| 5 | 12 | 1.0667 | 1.1167 | 1.1462 | 1.1880 | 6 | 1.2095 | 1.2093 | 1.1661 |
| 中位数 |  | 1.0725 | 1.1272 | 1.1427 | 1.1578 |  | 1.1870 | 1.1769 | 1.1758 |

**汇总:** K=2 的中位数 1.127,K=3 为 1.143,K=5 为 1.158(范围 [1.142, 1.192]);事后最佳 K 为 1.187(范围 [1.158, 1.210])。“填补了 greedy − best-of-N 差距的多大比例”(逐种子计算后取中位数):K=2 50%、K=3 65%、K=5 82%、事后最佳 K 96%。

**这个结果支持什么:** 把独立搜到的多个单函数赢家叠起来(没有失败反馈、没有种群、没有继承搜索),就能还原 greedy 与 best-of-N 之间**相当大一部分**差距(固定 K=5 约八成)。所以“greedy 更好”的很大一部分可以用**“保留并叠加多个函数的赢家”**解释。

**它不支持什么:** (1) 不证明差距的**全部**来自叠加:固定 K 的叠加仍低于 greedy 的中位数 1.176;事后最佳 K 看起来逼近甚至超过,但那是事后选择的最大值,有乐观偏差;(2) 不能分别证明**反馈、选择、继承**各自的贡献——没有逐项消融;(3) 叠加用的候选按搜索时 ratio 排序,而搜索时的 ratio 含噪声(§3.4),排序本身带选择偏差;(4) 叠加的候选与 greedy 链里的赢家来自同一批函数,二者并不独立;(5) 叠加补丁同样含有未同步的静态状态,见 §7:20 个叠加补丁的扩展正确性在 §7 总表中。
