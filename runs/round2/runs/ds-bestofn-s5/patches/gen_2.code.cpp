FIT_UINT16 Field::GetNumSubFields(void) const
{
    const Profile* p = profile;
    const FIT_UINT16 n = (p != NULL) ? p->numFields : 0;
    if (profileIndex < n)
        return p->fields[profileIndex].numSubFields;
    return 0;
}
