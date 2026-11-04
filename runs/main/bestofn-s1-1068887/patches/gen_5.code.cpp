
FIT_UINT16 Field::GetNumComponents(void) const
{
    if (!profile || profileIndex >= profile->numFields)
        return 0;
    return profile->fields[profileIndex].numComponents;
}
