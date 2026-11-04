const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const std::array<const Profile::MESG*, 65536> lookup = []() {
        std::array<const Profile::MESG*, 65536> table{};
        for (int i = 0; i < MESGS; ++i)
        {
            if (table[mesgs[i].num] == nullptr)
                table[mesgs[i].num] = &mesgs[i];
        }
        return table;
    }();

    return lookup[num];
}
