
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static std::array<const Profile::MESG*, 65536> index;
    static bool initialized = false;
    if (!initialized) {
        index.fill(nullptr);
        for (int i = 0; i < MESGS; i++) {
            index[mesgs[i].num] = &mesgs[i];
        }
        initialized = true;
    }
    return index[num];
}
