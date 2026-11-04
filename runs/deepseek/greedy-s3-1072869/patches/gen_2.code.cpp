Field::Field(const Field &field)
    : FieldBase()
    , profile(field.profile)
    , profileIndex(field.profileIndex)
    , type(field.type)
    , isFieldExpanded(field.isFieldExpanded)
{
    fieldId = field.fieldId;
    size = field.size;
    numValues = field.numValues;
    std::memcpy(values, field.values, field.size);
}
