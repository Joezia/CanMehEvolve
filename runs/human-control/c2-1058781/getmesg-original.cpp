const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    for (int i = 0; i < MESGS; i++)
    {
        if (mesgs[i].num == num)
            return &mesgs[i];
    }

    return NULL;
}

