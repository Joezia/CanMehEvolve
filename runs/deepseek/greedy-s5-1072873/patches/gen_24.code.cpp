FIT_UINT16 Field::GetNumSubFields(void) const
{
    if (__builtin_expect((profile == NULL) || (profileIndex >= profile->numFields), 0))
        return 0;
    return profile->fields[profileIndex].numSubFields;
}
