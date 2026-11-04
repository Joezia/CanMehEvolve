const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* lut[65536] = {};
    static bool built = false;

    if (!built)
    {
        for (int i = 0; i < MESGS; i++)
        {
            if (lut[mesgs[i].num] == NULL)
                lut[mesgs[i].num] = &mesgs[i];
        }
        built = true;
    }

    return lut[num];
}
