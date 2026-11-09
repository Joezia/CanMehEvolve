
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Binary search over the already-sorted mesgs array (MESGS is small, typically <200)
    auto it = std::lower_bound(mesgs, mesgs + MESGS, num,
        [](const Profile::MESG& mesg, FIT_UINT16 value) {
            return mesg.num < value;
        });

    if (it != mesgs + MESGS && it->num == num)
        return it;

    return NULL;
}
