
```cpp
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* cached = nullptr;
    static FIT_UINT16 cached_num = 0xFFFF;

    if (cached && cached->num == num)
        return cached;

    cached = std::find_if(mesgs, mesgs + MESGS, [num](const Profile::MESG& m) { return m.num == num; });
    if (cached != mesgs + MESGS) {
        cached_num = num;
        return cached;
    }

    cached = nullptr;
    return nullptr;
}
