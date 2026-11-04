const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* table[65536] = {};
    static const bool initialized = []()
    {
        for (int i = 0; i < MESGS; i++)
        {
            if (table[mesgs[i].num] == NULL)
                table[mesgs[i].num] = &mesgs[i];
        }
        return true;
    }();
    (void)initialized;
    return table[num];
}
