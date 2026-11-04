const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const FIT_UINT16* const index = []() -> FIT_UINT16* {
        static FIT_UINT16 t[65536];
        for (int i = 0; i < 65536; ++i)
            t[i] = 0xFFFF;
        for (int i = MESGS - 1; i >= 0; --i)
            t[mesgs[i].num] = static_cast<FIT_UINT16>(i);
        return t;
    }();

    const FIT_UINT16 i = index[num];
    return (i == 0xFFFF) ? NULL : &mesgs[i];
}
