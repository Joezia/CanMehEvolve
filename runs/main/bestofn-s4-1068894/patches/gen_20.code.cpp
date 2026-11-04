
```cpp
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static std::vector<const Profile::MESG*> mesg_by_num;
    if (mesg_by_num.empty()) {
        mesg_by_num.resize(0x10000, nullptr);
        for (int i = 0; i < MESGS; i++) {
            mesg_by_num[mesgs[i].num] = &mesgs[i];
        }
    }
    return (num < mesg_by_num.size()) ? mesg_by_num[num] : nullptr;
}
