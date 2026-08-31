% run_fmu_simulink.m — co-simulate a ThrustLab FMI 3.0 FMU in Simulink.
%
% Builds a model programmatically, imports the bundled quadcopter FMU,
% commands a fixed throttle on every rotor, runs 30 s of co-simulation, and
% plots thrust, bus voltage, and battery state of charge.
%
% Requires MATLAB + Simulink (verified on R2025a). Run from this folder:
%
%     matlab -batch "run('run_fmu_simulink.m')"
%
% Three things that will silently ruin the model if changed (all measured):
%   * The FMU Import block lives in the Simulink Extras library
%     ('simulink_extras/FMU Import/FMU'), NOT in User-Defined Functions.
%   * The block wants a BARE file name with the FMU's folder on the MATLAB
%     path — a full path in FMUName is not accepted.
%   * Every FMU output you care about must be wired to a root Outport;
%     unconnected outputs are removed by block reduction and the simulation
%     proves nothing about them.
%
% Port order follows the FMU's modelDescription.xml declaration order and is
% the same for every ThrustLab export regardless of rotor count:
%   inputs : 1 throttle[N]  2 v_axial_m_s[N]  3 air_density_kg_m3
%            4 v_edge_m_s[N]  5 ambient_temp_C  6 v_body_m_s
%            7 omega_body_rad_s  8 tilt_rad[N]  9 wind_m_s
%   outputs: 1 thrust_N[N]  2 torque_Nm[N]  3 force_inplane_N[N]  4 rpm[N]
%            5 current_A[N]  6 motor_temp_C[N]  7 voltage_bus_V
%            8 current_bus_A  9 power_bus_W  10 battery_soc
%            11 battery_temp_C  12 force_total_N  13 moment_total_Nm
%            14 sub_steps  (+ per-rotor envelope flags and the rotor manifest)

FMU_FILE = 'validation-quad.fmu';   % bundled one folder up
N_ROTORS = 4;                       % rotor count of THIS FMU
THROTTLE = 0.65;                    % commanded on every rotor, 0..1
STOP_S   = 30;

here = fileparts(mfilename('fullpath'));
addpath(fullfile(here, '..'));      % FMU block needs the folder on the path

mdl = 'tl_fmu_cosim';
try close_system(mdl, 0); catch, end
new_system(mdl);
blk = [mdl '/powertrain'];
load_system('simulink_extras');
add_block('simulink_extras/FMU Import/FMU', blk);
set_param(blk, 'FMUName', FMU_FILE);
ph = get_param(blk, 'PortHandles');
fprintf('FMU ports: %d in, %d out\n', numel(ph.Inport), numel(ph.Outport));

% Drive throttle (input 1, an N-wide array) and air density (input 3).
add_block('simulink/Sources/Constant', [mdl '/throttle'], ...
    'Value', sprintf('%g*ones(1,%d)', THROTTLE, N_ROTORS));
add_block('simulink/Sources/Constant', [mdl '/rho'], 'Value', '1.225');
th = get_param([mdl '/throttle'], 'PortHandles');
rh = get_param([mdl '/rho'], 'PortHandles');
add_line(mdl, th.Outport(1), ph.Inport(1));
add_line(mdl, rh.Outport(1), ph.Inport(3));

% Root Outports on every FMU output (see the block-reduction note above).
for p = 1:numel(ph.Outport)
    op = sprintf('%s/out%d', mdl, p);
    add_block('simulink/Sinks/Out1', op);
    oph = get_param(op, 'PortHandles');
    add_line(mdl, ph.Outport(p), oph.Inport(1));
end

set_param(mdl, 'StopTime', num2str(STOP_S), ...
    'SolverType', 'Fixed-step', 'FixedStep', '0.01');
out = sim(mdl);
y = out.yout;

thrust  = y{1}.Values;   % thrust_N, N columns
voltage = y{7}.Values;   % voltage_bus_V
soc     = y{10}.Values;  % battery_soc

fprintf('final per-rotor thrust [N]: %s\n', mat2str(thrust.Data(end, :), 5));
fprintf('final bus voltage [V]:      %.3f\n', voltage.Data(end));
fprintf('final state of charge:      %.4f\n', soc.Data(end));

fig = figure('Visible', 'off', 'Position', [0 0 900 700]);
subplot(3, 1, 1);
plot(thrust.Time, thrust.Data); grid on;
ylabel('thrust [N]'); title(sprintf('%s at %.0f%% throttle', FMU_FILE, 100 * THROTTLE));
subplot(3, 1, 2);
plot(voltage.Time, voltage.Data); grid on;
ylabel('bus voltage [V]');
subplot(3, 1, 3);
plot(soc.Time, soc.Data); grid on;
ylabel('state of charge'); xlabel('time [s]');
saveas(fig, fullfile(here, 'fmu_cosim.png'));
fprintf('wrote %s\n', fullfile(here, 'fmu_cosim.png'));

close_system(mdl, 0);
disp('FMU_COSIM_DONE');
