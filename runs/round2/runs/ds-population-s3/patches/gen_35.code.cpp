const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* table[65536] = { 0 };
    static bool init = false;

    const Profile::MESG* mesg = table[num];
    if (mesg == nullptr)
    {
        if (!init)
        {
            for (int i = MESGS - 1; i >= 0; i--)
                table[mesgs[i].num] = &mesgs[i];
            init = true;
        }
        mesg = table[num];
    }

    return mesg;
}
