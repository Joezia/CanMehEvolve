FIT_BOOL Field::GetIsAccumulated() const
{
    const Profile* const p = profile;
    return p->fields[profileIndex].isAccumulated;
}
