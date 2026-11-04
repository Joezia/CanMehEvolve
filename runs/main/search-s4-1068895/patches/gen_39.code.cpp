
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    for (const auto* it = mesgs, *end = mesgs + MESGS; it != end; ++it)
        if (it->num == num)
            return it;
    return NULL;
}
