FieldBase::FieldBase(const FieldBase &field)
{
    values.swap(const_cast<std::vector<FitValue> &>(field.values));
    stringIndexes.swap(const_cast<std::vector<FIT_STRING_INDEX> &>(field.stringIndexes));
}
