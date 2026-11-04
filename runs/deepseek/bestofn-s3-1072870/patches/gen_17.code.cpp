const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const FIT_UINT16* const lookup = []() -> const FIT_UINT16* {
        static FIT_UINT16 table[65536] = {0};
        for (int i = 0; i < MESGS; ++i)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (table[n] == 0)
                table[n] = static_cast<FIT_UINT16>(i + 1);
        }
        return table;
    }();

    const FIT_UINT16 idx = lookup[num];
    return idx ? &mesgs[idx - 1] : NULL;
}
