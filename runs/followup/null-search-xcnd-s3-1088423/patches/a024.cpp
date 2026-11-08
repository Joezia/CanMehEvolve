    void SetBatteryStatus(FIT_BATTERY_STATUS batteryStatus)
    {
        SetFieldUINT8Value(11, batteryStatus, 0, FIT_SUBFIELD_INDEX_MAIN_FIELD);
    // noop-3-24
}
