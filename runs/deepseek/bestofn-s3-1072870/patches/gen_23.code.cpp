FIT_UINT16 Field::GetNumSubFields(void) const
{
    if (__builtin_expect(profile == NULL, 0) ||
        __builtin_expect(profileIndex >= profile->numFields, 0))
        return 0;
    return profile->fields[profileIndex].numSubFields;
}
