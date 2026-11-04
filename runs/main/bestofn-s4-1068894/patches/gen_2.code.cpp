
```cpp
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static std::vector<const Profile::MESG*> index(65536, nullptr);
    static bool initialized = false;
    if (!initialized) {
        for (int i = 0; i < MESGS; i++) {
            index[mesgs[i].num] = &mesgs[i];
        }
        initialized = true;
    }
    return index[num];
}
