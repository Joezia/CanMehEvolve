FIT_UINT8 Field::GetNum(void) const
{
    const Profile* p = profile;
    if (p == NULL)
        return FIT_FIELD_NUM_INVALID;
    return (profileIndex < p->numFields) ? p->fields[profileIndex].num : FIT_FIELD_NUM_INVALID;
}
