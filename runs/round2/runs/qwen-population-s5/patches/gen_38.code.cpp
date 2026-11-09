
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static std::array<const Profile::MESG*, 0x10000> lookup{};
    static bool initialized = false;
    if (!initialized) {
        for (int i = 0; i < MESGS; i++) {
            lookup[mesgs[i].num] = &mesgs[i];
        }
        initialized = true;
    }
    return lookup[num];
}
