const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* table[65536] = {};
    static bool init = false;

    if (!init)
    {
        for (int i = 0; i < MESGS; i++)
        {
            if (!table[mesgs[i].num])
                table[mesgs[i].num] = &mesgs[i];
        }
        init = true;
    }

    return table[num];
}
