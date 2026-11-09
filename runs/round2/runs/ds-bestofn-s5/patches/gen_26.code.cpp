const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const std::array<const MESG*, 65536> table = [] {
        std::array<const MESG*, 65536> t{};
        for (int i = 0; i < MESGS; i++)
        {
            if (t[mesgs[i].num] == nullptr)
                t[mesgs[i].num] = &mesgs[i];
        }
        return t;
    }();

    return table[num];
}
