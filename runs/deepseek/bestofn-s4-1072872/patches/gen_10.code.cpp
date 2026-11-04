const Profile::FIELD_COMPONENT* Field::GetComponent(const FIT_UINT16 component) const
{
    if (component >= GetNumComponents())
        return NULL;
    return profile->fields[profileIndex].components + component;
}
