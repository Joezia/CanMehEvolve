const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const std::array<const Profile::MESG*, 65536> lookup = [] {
        std::array<const Profile::MESG*, 65536> table{};
        for (int i = 0; i < MESGS; ++i)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (table[n] == nullptr)
                table[n] = &mesgs[i];
        }
        return table;
    }();

    return lookup[num];
}
