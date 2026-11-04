
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    const Profile::MESG* result = std::lower_bound(mesgs, mesgs + MESGS, num,
        [](const Profile::MESG& mesg, FIT_UINT16 val) { return mesg.num < val; });
    return (result != mesgs + MESGS && result->num == num) ? result : nullptr;
}
