```cpp
FIT_UINT16 Field::GetNumSubFields(void) const
{
    const Profile* p = profile;
    if (p == NULL || profileIndex >= p->numFields)
        return 0;
    return p->fields[profileIndex].numSubFields;
}
