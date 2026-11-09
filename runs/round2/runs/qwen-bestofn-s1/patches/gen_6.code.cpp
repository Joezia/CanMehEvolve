
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Use std::find_if with a lambda for potential compiler optimization
    // and to maintain identical behavior while enabling better inlining
    const auto it = std::find_if(mesgs, mesgs + MESGS,
        [num](const MESG& m) { return m.num == num; });
    return (it != mesgs + MESGS) ? &*it : NULL;
}
