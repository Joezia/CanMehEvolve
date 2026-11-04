FIT_UINT16 Field::GetNumSubFields(void) const
{
    const Profile::Field* f = profile ? &profile->fields[profileIndex] : NULL;
    if ((f == NULL) || (profileIndex >= profile->numFields))
        return 0;
    return f->numSubFields;
}
