const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const MESG* table[65536] = {};
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = MESGS - 1; i >= 0; --i)
        {
            table[mesgs[i].num] = &mesgs[i];
        }
        initialized = true;
    }

    return table[num];
}
